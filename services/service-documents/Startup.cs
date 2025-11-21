using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.OpenApi.Models;
using System;
using System.Text.Json;

namespace ServiceDocuments
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllers();
            
            // CORS
            services.AddCors(options =>
            {
                options.AddPolicy("AllowAll",
                    builder =>
                    {
                        builder.AllowAnyOrigin()
                               .AllowAnyMethod()
                               .AllowAnyHeader();
                    });
            });

            // Swagger
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo
                {
                    Title = "Service Documents API",
                    Version = "v1",
                    Description = "Gestion et stockage des documents médicaux"
                });
            });

            // Health Checks
            services.AddHealthChecks();

            // Configuration MinIO
            var minioEndpoint = Configuration["MinIO:Endpoint"] ?? "localhost:9000";
            var minioAccessKey = Configuration["MinIO:AccessKey"] ?? "minio_admin";
            var minioSecretKey = Configuration["MinIO:SecretKey"] ?? "minio_password";

            Console.WriteLine($"MinIO Configuration: {minioEndpoint}");
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseSwagger();
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint("/swagger/v1/swagger.json", "Service Documents API V1");
                c.RoutePrefix = "swagger";
            });

            app.UseRouting();
            app.UseCors("AllowAll");
            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
                endpoints.MapHealthChecks("/health");
                
                // Root endpoint
                endpoints.MapGet("/", async context =>
                {
                    context.Response.ContentType = "application/json";
                    await context.Response.WriteAsync(System.Text.Json.JsonSerializer.Serialize(new
                    {
                        service = "documents-service",
                        version = "1.0.0",
                        status = "healthy",
                        timestamp = DateTime.UtcNow
                    }));
                });
            });
        }
    }
}
